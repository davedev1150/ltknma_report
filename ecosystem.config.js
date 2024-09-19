module.exports = {
    apps : [{
      name: 'flask_backend_test',
      script: 'src/app.py',
      interpreter: 'python3',
      env: {
        ENV: 'test' // This environment variable will be applied
      }
    },{
      name: 'flask_backend_prod',
      script: 'src/app.py',
      interpreter: 'python3',
      env: {
        ENV: 'prod' // This environment variable will be applied
      }
    }]
  };
  