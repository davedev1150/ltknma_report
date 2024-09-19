**GIT**
sudo git clone https://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@github.com/davedev1150/flask_micro_app.git
password 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

***docker***
- sudo docker-compose up -d

-python3 src/app.py
ENV="test" python3 src/app.py
ENV="dev" DOMAIN_URL="http://localhost:1153" python3 src/app.py

-sudo pm2 start --name "flask_backend_test" -- run "ENV="test" python3 src/app.py"
sudo pm2 start ecosystem.config.js --env test
flask_backend_prod