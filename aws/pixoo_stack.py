import os

from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class PixooStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pixoo_lambda = PythonFunction(
            self,
            "PixooHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            entry="../local",
            index="index.py",
            handler="lambda_handler",
            timeout=Duration.seconds(10),
            environment={
                "PIXOO_URL": os.environ["PIXOO_URL"],
            },
        )

        rule = events.Rule(
            self,
            "EveryMinuteRule",
            schedule=events.Schedule.rate(Duration.minutes(1)),
        )

        # 3. Add the Lambda as a target for the rule
        rule.add_target(targets.LambdaFunction(pixoo_lambda))

        fn_url = pixoo_lambda.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )

        CfnOutput(self, "PixooUrl", value=fn_url.url)
        CfnOutput(self, "DeploymentRegion", value=self.region)
