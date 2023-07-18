import json
import time
import boto3

forecast_client = boto3.client('forecast')
forecast_role_arn = 'arn:aws:iam::811219959239:role/ForecastRole'
target_time_series = 'target_value'
forecast_name = 'currency-forecast'
predictor_name = 'currency-predictor'
algorithm_arn = 'arn:aws:forecast:::algorithm/Prophet'

def lambda_handler(event, context):
    s3_bucket = 'forecast-data-6998'
    s3_key = "currency_records.csv"

    dataset_group_name = f"{s3_key}_dataset_group"
    dataset_name = f"{s3_key}_dataset"
    schema = {
        "Attributes": [
            {"AttributeName": "item_id", "AttributeType": "string"},
            {"AttributeName":"timestamp", "AttributeType":"timestamp"},
            {"AttributeName":"target_value", "AttributeType":"float"}
        ]
    }
    response = forecast_client.create_dataset_group(
        DatasetGroupName=dataset_group_name,
        Domain="CUSTOM",
        RoleArn=forecast_role_arn
    )
    print(f"Dataset Group Arn: {response['DatasetGroupArn']}")

    response = forecast_client.create_dataset(
        DatasetName=dataset_name,
        Domain="CUSTOM",
        DatasetType='TARGET_TIME_SERIES',
        DataFrequency='D',
        Schema=schema,
        S3Config={
            'Path': f"s3://{s3_bucket}/{s3_key}",
            'RoleArn': forecast_role_arn
        }
    )
    print(f"Dataset Arn: {response['DatasetArn']}")

    response = forecast_client.create_dataset_import_job(
        DatasetImportJobName=f"{s3_key}_import_job",
        DatasetArn=response['DatasetArn'],
        DataSource={
            'S3Config': {
                'Path': f"s3://{s3_bucket}/{s3_key}",
                'RoleArn': forecast_role_arn
            }
        },
        TimestampFormat='yyyy-MM-dd'
    )
    print(f"Dataset Import Job Arn: {response['DatasetImportJobArn']}")

    while True:
        response = forecast_client.describe_dataset_import_job(
            DatasetImportJobArn=response['DatasetImportJobArn']
        )
        status = response["Status"]
        print(f"Dataset Import Job Status: {status}")
        if status == "ACTIVE":
            break
        time.sleep(30)

    response = forecast_client.create_predictor(
        PredictorName=predictor_name,
        # AlgorithmArn=algorithm_arn,
        ForecastHorizon=7,  #number of days to predict
        PerformAutoML=True,
        InputDataConfig={
            "DatasetGroupArn": response['DatasetGroupArn'],
        },
        # FeaturizationConfig={
        #     "ForecastFrequency": "D",
        #     "Featurizations": [
        #         {
        #             "AttributeName": "target_value",
        #             "FeaturizationPipeline": [
        #                 {
        #                     "FeaturizationMethodName": "filling",
        #                     "FeaturizationMethodParameters": {
        #                         "frontfill": "none",
        #                         "middlefill": "zero",
        #                         "backfill": "zero"
        #                     }
        #                 }
        #             ]
        #         }
        #     ]
        # },
        # TrainingParameters={
        #     "context_length": "14",
        #     "learning_rate": "0.001",
        #     "max_epochs": "500",
        #     "num_cells": "64",
        #     "num_layers": "2",
        #     "prediction_length": "14",
        #     "dropout_rate": "0.2"
        # }
    )
    print(f"Predictor Arn: {response['PredictorArn']}")

    while True:
        response = forecast_client.describe_predictor(
            PredictorArn=response['PredictorArn']
        )
        status = response["Status"]
        print(f"Predictor Status: {status}")
        if status == "ACTIVE":
            break
        time.sleep(30)

    forecast_response = forecast_client.create_forecast(
        ForecastName=forecast_name,
        PredictorArn=response['PredictorArn'],
        ForecastTypes=['mean', 'p10', 'p50', 'p90']
    )
    print(f"Forecast Arn: {forecast_response['ForecastArn']}")

    while True:
        response = forecast_client.describe_forecast(
            ForecastArn=forecast_response['ForecastArn']
        )
        status = response["Status"]
        print(f"Forecast Status: {status}")
        if status == "ACTIVE":
            break
        time.sleep(30)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
