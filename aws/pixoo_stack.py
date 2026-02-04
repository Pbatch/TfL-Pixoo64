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
            runtime=_lambda.Runtime.PYTHON_3_14,
            entry="../local",
            index="index.py",
            handler="lambda_handler",
            timeout=Duration.seconds(10),
            environment={
                "PIXOO_URL": os.environ["PIXOO_URL"],
                "TFL_APP_KEY": os.environ["TFL_APP_KEY"],
            },
        )

        pixoo_rule = events.Rule(
            self,
            "PixooRule",
            schedule=events.Schedule.rate(Duration.minutes(1)),
        )
        pixoo_rule.add_target(targets.LambdaFunction(pixoo_lambda))

        CfnOutput(self, "PixooRegion", value=self.region)