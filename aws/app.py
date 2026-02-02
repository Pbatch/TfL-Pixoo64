import aws_cdk as cdk
from pixoo_stack import PixooStack

app = cdk.App()
PixooStack(app, "PixooBridgeStack")

app.synth()
