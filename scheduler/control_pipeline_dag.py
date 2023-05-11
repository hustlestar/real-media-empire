import asyncio
import time
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from telegram import Bot

# Replace with your own values
TELEGRAM_API_TOKEN = '1439670844:AAFejYbp5TSMcuWMW_TxUDSKiho1Ht7gc7w'
CHAT_IDS = ['66395090']


def call_api_and_check_status(cmd=None, ts=None, msg=None, timeout=60 * 60):
    # Replace with your REST API URL
    api_url = 'http://winhost:10101/commands'

    print(f"Received \ncmd: {cmd}\nts: {ts}")

    if ts:
        ts = datetime.fromisoformat(ts)
        formatted_ts = ts.strftime('%Y%m%d%H%M%S')
        cmd = cmd.replace('[ym_ts]', formatted_ts)
        print(f"New cmd:\n{cmd}")

    response = requests.post(api_url, json=dict(command=cmd))
    initil_response_json = response.json()
    status = initil_response_json.get('command_status')
    print(f"Initial response from API: \n{initil_response_json}")
    start_time = time.time()
    timeout = 60 * 60 if not timeout else timeout
    print(f"Starting with timeout {timeout}")
    is_failed = False
    stdout, stderr = None, None
    try:
        while True:
            response = requests.get(f"{api_url}/{initil_response_json.get('command_id')}")
            response_json = response.json()
            print(f"{response_json.get('command_id')} Command status from API is: {response_json.get('command_status')}")
            status = response_json.get('command_status')
            stdout, stderr = response_json.get('stdout'), response_json.get('stderr')
            elapsed_time = time.time() - start_time

            if status in ('success'):
                break
            elif status in ('failed', 'error'):
                raise Exception(f"Command failed with status: {status}")
            elif elapsed_time >= timeout:
                print("Timeout reached! Exiting...")
                raise TimeoutError(f"Timeout reached! Exiting...")
            elif status == 'running':
                print("Command still running. Waiting...")
                time.sleep(60)  # Wait 1 minute before checking again
    except Exception as x:
        is_failed = True
        print(x)

    try:
        bot_message = prepare_msg(msg, status, stderr=stderr)
        asyncio.run(send_telegram_message(bot_message))
    except Exception as x:
        print(x)
    if is_failed:
        print(f"stdout: \n{stdout}")
        print(f"stderr: \n{stderr}")
        raise Exception(f"Failed to run command!")


def prepare_msg(msg, status, stdout=None, stderr=None):
    if status != 'success':
        message = f"{msg}: {status}\nstdout:\n{stdout[-2000:] if stdout else ''}\nstderr:\n{stderr[-2000:] if stderr else ''}"
    else:
        message = f"{msg}: {status}"
    return message


async def send_telegram_message(message, **kwargs):
    bot = Bot(token=TELEGRAM_API_TOKEN)

    for chat_id in CHAT_IDS:
        await bot.send_message(chat_id=chat_id, text=message)


def generate_dag(dag_id, schedule_interval, **kwargs):
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 0,
        'retry_delay': timedelta(minutes=1),
    }

    dag = DAG(
        dag_id,
        default_args=default_args,
        description=f"DAG that calls a REST API with cmd={kwargs.get('cmd')} and sends a Telegram message",
        schedule_interval=schedule_interval,
        start_date=datetime(2023, 5, 1),
        catchup=False,
    )

    api_task = PythonOperator(
        task_id='run_command_and_check_status',
        python_callable=call_api_and_check_status,
        op_kwargs={'cmd': kwargs.get('cmd'), 'msg': kwargs.get('custom_message'), 'ts': '{{ ts }}', 'timeout': kwargs.get('timeout')},
        execution_timeout=timedelta(hours=8),  # Set the timeout for this task
        dag=dag,
    )

    return dag


# Create multiple DAGs with different cmd and schedule_interval values
class ChannelDAGConfig:
    def __init__(self, dag_id, schedule_interval, **kwargs):
        self.dag_id = dag_id
        self.schedule_interval = schedule_interval
        self.kwargs = kwargs


dag_configs = [
    ChannelDAGConfig(
        dag_id='infinite_quotes_inspiration__generate',
        schedule_interval='0 2 * * *',
        cmd='set PYTHONPATH=%PYTHONPATH%;G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\ &'
            ' C:\\Users\\hustlestar\\Anaconda3\\envs\\media-empire\\python.exe "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\pipelines\\quotes_generate.py"'
            ' --channel_config_path "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\infinite_quotes_inspiration.yaml"'
            ' --execution_date [ym_ts]',
        custom_message='Infinite Quotes Inspiration #QUOTES_VIDEO_GENERATE pipeline finished with status: ',
        timeout=25200
    ),
    ChannelDAGConfig(
        dag_id='infinite_quotes_inspiration__publish',
        schedule_interval='0 13 * * *',
        cmd='set PYTHONPATH=%PYTHONPATH%;G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\ &'
            ' C:\\Users\\hustlestar\\Anaconda3\\envs\\media-empire\\python.exe "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\pipelines\\publish_pipeline.py"'
            ' --channel_config_path "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\infinite_quotes_inspiration.yaml"'
            ' --execution_date [ym_ts]',
        custom_message='Infinite Quotes Inspiration #QUOTES_PUBLISH pipeline finished with status: '
    ),
    ChannelDAGConfig(
        dag_id='daily_mindset__video',
        schedule_interval='0 9 * * 1,4,6',
        cmd='set PYTHONPATH=%PYTHONPATH%;G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\ &'
            ' C:\\Users\\hustlestar\\Anaconda3\\envs\\media-empire\\python.exe "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\pipelines\\basic_you_tube_pipeline.py"'
            ' --channel_config_path "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\daily_mindset.yaml"'
            ' --execution_date [ym_ts]',
        custom_message='Daily Mindset #BASIC_VIDEO pipeline finished with status: '
    ),
    ChannelDAGConfig(
        dag_id='century_wisdom__video',
        schedule_interval='0 11 * * 2,5,7',
        cmd='set PYTHONPATH=%PYTHONPATH%;G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\ &'
            ' C:\\Users\\hustlestar\\Anaconda3\\envs\\media-empire\\python.exe "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\pipelines\\basic_you_tube_pipeline.py"'
            ' --channel_config_path "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\century_wisdom.yaml"'
            ' --execution_date [ym_ts]',
        custom_message='Century Wisdom #BASIC_VIDEO pipeline finished with status: '
    ),
    ChannelDAGConfig(
        dag_id='daily_mindset__shorts_generate',
        schedule_interval="0 14 * * 5",
        cmd='set PYTHONPATH=%PYTHONPATH%;G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\ &'
            ' C:\\Users\\hustlestar\\Anaconda3\\envs\\media-empire\\python.exe "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\pipelines\\shorts_generate.py"'
            ' --channel_config_path "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\daily_mindset_shorts.yaml"'
            ' --number_of_videos 32',
        custom_message='Daily Mindset #SHORTS_SWAMP pipeline finished with status: ',
        timeout=25200
    ),
    ChannelDAGConfig(
        dag_id='daily_mindset__shorts_publish',
        schedule_interval="0 0,8,16 * * *",
        cmd='set PYTHONPATH=%PYTHONPATH%;G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\ &'
            ' C:\\Users\\hustlestar\\Anaconda3\\envs\\media-empire\\python.exe "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src\\pipelines\\shorts_publish.py"'
            ' --channel_config_path "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\jack\\daily_mindset_shorts.yaml"',
        custom_message='Daily Mindset #SHORTS_PUBLISH pipeline finished with status: '
    ),
]

for config in dag_configs:
    globals()[config.dag_id] = generate_dag(config.dag_id, config.schedule_interval, **config.kwargs)
