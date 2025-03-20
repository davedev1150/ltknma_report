import requests
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import traceback
from service.report import Main
from dotenv import load_dotenv
import os
import pytz
import pymsteams

THAI_TZ = pytz.timezone('Asia/Bangkok')
app = Flask(__name__)

CORS(app)
load_dotenv()

ENV = os.getenv("ENV")
port = 2512

DOMAIN_URL = "http://localhost:2512"
if ENV == "prod":
    DOMAIN_URL = "http://nasgfe1.synology.me:2512"

print("App started successfully." + DOMAIN_URL)
print(port)


@app.route('/', methods=['GET'])
def get_data():
    # Your logic to retrieve or process data
    data = {"message": "Hello from Python microservice! Generate LTKNMA Report!"}

    return jsonify(data)


@app.route('/report', methods=['GET'])
def get_report_data():
    print("Fetching data...")
    report_path = Main()
    if report_path is None:
        return jsonify({"message": "Failed to generate report"}), 500
    else:
        return send_file(report_path, as_attachment=True, mimetype='application/pdf')


# Function to run the Main() function
def send_line_notification(message):
    url = 'https://notify-api.line.me/api/notify'
    # Replace with your actual LINE Notify token
    token = 'hCCDUEMUbYWDWmYln9LubNa6CkmfuGZLCrDoKSsv8zz'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {token}'
    }
    data = {'message': message}

    # Send the POST request to LINE Notify API
    response = requests.post(url, headers=headers, data=data)

    # Check the response
    if response.status_code == 200:
        print('Notification sent successfully!')
    else:
        print(
            f'Failed to send notification. Status code: {response.status_code}')
        print(response.text)


def send_adaptive_card_to_teams(webhook_url, message):
    adaptive_card_json = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": f"Daily Dam Monitoring Report (ลำตะคอง)",
        "themeColor": "FF0000",
        "sections": [{
            "activityTitle": "🚨 <font color='#992900'><b>**Daily Dam Monitoring Report**</b></font>",
            "facts": [
                {"name": "URL:", "value": message},
            ],
            "markdown": True
        }]
    }

    try:
        teams_message = pymsteams.connectorcard(webhook_url)
        teams_message.payload = adaptive_card_json
        teams_message.send()
        print("Adaptive card notification sent successfully.")
    except Exception as e:
        print(f"Failed to send adaptive card: {e}")


@app.route('/get-file/<path:filename>')
def serve_file(filename):
    SRCDIR = os.path.dirname(os.path.abspath(__file__))
    print("SRCDIR", SRCDIR)
    file_path = os.path.join(
        SRCDIR, "service/", filename)
    return send_file(file_path, as_attachment=True, mimetype='application/pdf')


def scheduled_report():
    try:
        print("Running scheduled report...")
        webhook_url = "https://teamgrouppcl.webhook.office.com/webhookb2/c6cb0e26-e275-4b88-8f81-108a668ec06c@e13fef33-a530-4c08-b4d5-2e4711280b4d/IncomingWebhook/52c1f551509f424ea72dd7965f659295/dd59822a-dd77-48a9-b011-21c03af65368/V2mfv6qafKkzygJewXjW5HGtTN90yOm1u2drSsq-U5bkk1"
        report_path = Main()
        message = "Daily Dam Monitoring Report"
        if report_path is None:
            message += "\nFailed to generate report"
        else:
            file_name = report_path.split("/")[-1]
            url = DOMAIN_URL + "/get-file/" + file_name
            message += f"\n{url}"

        send_adaptive_card_to_teams(webhook_url,message)
        print("Report generated successfully.")
    except Exception as e:
        print(f"Error generating reports: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    # Initialize the background scheduler
    scheduler = BackgroundScheduler()

    scheduled_report()

    # Schedule the task to run every day at 3 AM in Thailand time (ICT, UTC+7)
    scheduler.add_job(scheduled_report, CronTrigger(
        hour=6, minute=0, timezone=THAI_TZ))

    # Schedule the task to run every 10 minutes
    # scheduler.add_job(scheduled_report, 'interval', minutes=10)

    print(scheduler.get_jobs())  # Print all jobs in the scheduler
    # Start the scheduler
    scheduler.start()

    try:
        # Start the Flask app

        app.run(host='0.0.0.0', port=port, use_reloader=False, debug=True)

    except (KeyboardInterrupt, SystemExit):
        # Shut down the scheduler when exiting the app
        scheduler.shutdown()
