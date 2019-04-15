import unittest2 as unittest
import yaml
from mock import patch, MagicMock
from botocore.exceptions import ClientError

from .fixtures import BotoSessionFixture, clone_test_state
from greengo import greengo
from greengo.lambdas import Lambdas
from greengo.state import State

# logging.basicConfig(
#     format='%(asctime)s|%(name).10s|%(levelname).5s: %(message)s',
#     level=logging.DEBUG)

# Do not override the production state, work with testing state.
greengo.STATE_FILE = '.gg_state_test.json'

lambdas_yaml = '''
Group:
    name: my_group
Lambdas:
  - name: GreengrassHelloWorld
    runtime: Python2.7
    handler: function.handler
    package: lambdas/GreengrassHelloWorld
    alias: dev
    environment:
      foo: bar
    greengrassConfig:
      MemorySize: 128000 # Kb, ask AWS why
      Timeout: 10 # Sec
      Pinned: True # Set True for long-lived functions
      Environment:
        AccessSysfs: False
        ResourceAccessPolicies:
          - ResourceId: 1_path_to_input
            Permission: 'rw'
        Variables:
           name: value
'''


class LambdasTest(unittest.TestCase):
    def setUp(self):
        self.group = yaml.safe_load(lambdas_yaml)
        with patch.object(greengo.session, 'Session', BotoSessionFixture) as f:
            self.boto_session = f
            self.gg = greengo.Commands()

    def tearDown(self):
        pass

    def test_lambda_create(self):
        group = self.group
        state = clone_test_state()
        functions = state.get('Lambdas.Functions')
        function_def = state.get('Lambdas.FunctionDefinition')
        lambda_role = state.get('Lambdas.LambdaRole')

        state.remove('Lambdas')

        Lambdas(group, state)._do_create()

        self.assertEqual(
            state.get('Lambdas.Functions')[0]['FunctionArn'],
            functions[0]['FunctionArn'])
        self.assertDictEqual(
            state.get('Lambdas.FunctionDefinition'),
            function_def
        )
        self.assertDictEqual(
            state.get('Lambdas.LambdaRole'),
            lambda_role
        )

    def test_default_lambda_role_arn__already_created(self):
        group = self.group
        state = clone_test_state()
        arn = Lambdas(group, state)._default_lambda_role_arn()
        self.assertEqual(arn, state.get('Lambdas.LambdaRole.Role.Arn'))

    def test_default_lambda_role_arn__create(self):
        group = self.group
        arn = clone_test_state().get('Lambdas.LambdaRole.Role.Arn')
        state = State(file=None)
        arn = Lambdas(group, state)._default_lambda_role_arn()
        self.assertEqual(arn, state.get('Lambdas.LambdaRole.Role.Arn'))

    def test_default_lambda_role_arn__previously_defined(self):
        group = self.group
        la = Lambdas(group, State(file=None))
        error = ClientError(
            error_response={'Error': {'Code': 'EntityAlreadyExists'}},
            operation_name='CreateRole')

        la._iam.create_role = MagicMock(side_effect=error)
        arn = la._default_lambda_role_arn()  # Doesn't blow up
        self.assertIsNotNone(arn)

    def test_lambda_remove(self):
        group = self.group
        state = clone_test_state()

        self.assertTrue(state.get('Lambdas.Functions'))
        self.assertTrue(state.get('Lambdas.FunctionDefinition'))
        self.assertTrue(state.get('Lambdas.LambdaRole'))

        la = Lambdas(group, state)

        with patch('os.remove'):
            # import pdb; pdb.set_trace()
            la._do_remove()

        self.assertTrue(la._lambda.delete_function.called)
        self.assertTrue(la._gg.delete_function_definition.called)
        self.assertFalse(state.get('Lambdas.Functions'))
        self.assertFalse(state.get('Lambdas.FunctionDefinition'))
        self.assertFalse(state.get('Lambdas.LambdaRole'))

    def test_lambda_remove__no_function_definitions(self):
        group = self.group
        state = clone_test_state()
        self.assertTrue(state.get('Lambdas.FunctionDefinition'))
        state.remove('Lambdas.FunctionDefinition')

        la = Lambdas(group, state)
        with patch('os.remove'):
            la._do_remove()

        self.assertTrue(la._lambda.delete_function.called)
        self.assertFalse(la._gg.delete_function_definition.called)
