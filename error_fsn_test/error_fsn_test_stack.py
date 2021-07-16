from aws_cdk import core as cdk
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
import aws_cdk.aws_lambda as lambda_
from aws_cdk.core import Duration


from aws_cdk import core


class ErrorFsnTestStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        submit_lambda = lambda_.Function(
            self, id='SubmitLambda',
            function_name='SubmitLambda',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.asset('lambda'),
            handler='submitjob.lambda_handler',
        )

        get_status_lambda = lambda_.Function(
            self, id='GetStatusLambda',
            function_name='GetStatusLambda',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.asset('lambda'),
            handler='getstatus.lambda_handler',
        )

        print_error_lambda = lambda_.Function(
            self, id='PrintErrorLambda',
            function_name='PrintErrorLambda',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.asset('lambda'),
            handler='printerror.lambda_handler',
        )



        # The code that defines your stack goes here
        submit_job = tasks.LambdaInvoke(self, "Submit Job",
                                        lambda_function=submit_lambda,
                                        # Lambda's result is in the attribute `Payload`
                                        output_path="$.Payload"
                                        )

        wait_x = sfn.Wait(self, "Wait X Seconds",
                          time=sfn.WaitTime.seconds_path("$.waitSeconds")
                          )

        get_status = tasks.LambdaInvoke(self, "Get Job Status",
                                        lambda_function=get_status_lambda,
                                        # Pass just the field named "guid" into the Lambda, put the
                                        # Lambda's result in a field called "status" in the response
                                        input_path="$.guid",
                                        output_path="$.Payload"
                                        )


        job_failed = sfn.Fail(self, "Job Failed",
                              cause="AWS Batch Job Failed",
                              error="DescribeJob returned FAILED"
                              )

        error_fail = sfn.Fail(self, "Error ",
                              cause="AWS Batch Job Failed",
                              error="DescribeJob returned FAILED"
                              )

        print_error = tasks.LambdaInvoke(self, "Print Error",
                                        lambda_function=print_error_lambda,
                                        # Pass just the field named "guid" into the Lambda, put the
                                        # Lambda's result in a field called "status" in the response
                                        output_path="$.Payload"
                                        )
        handling_error= print_error.next(error_fail)


        get_status = get_status.add_catch(handling_error)

        final_status = tasks.LambdaInvoke(self, "Get Final Job Status",
                                          lambda_function=get_status_lambda,
                                          # Use "guid" field as input
                                          input_path="$.guid",
                                          output_path="$.Payload"
                                          )

        definition = submit_job.next(wait_x).next(get_status).next(
            sfn.Choice(self, "Job Complete?").when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed).when(
                sfn.Condition.string_equals("$.status", "\"SUCCEEDED\""), final_status).otherwise(wait_x))



        sfn.StateMachine(self, "StateMachine",
                         definition=definition,
                         timeout=Duration.minutes(1)
                         )
