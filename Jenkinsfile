node('docker && mysql') {
    try{
        currentBuild.result = 'SUCCESS'
        stage('Checkout'){
            deleteDir()
            checkout scm
            withCredentials([file(credentialsId: 'autotraderweb_v3', variable: 'FILE')]) {
                sh 'cp ${FILE} config.ini'
            }
        }

        stage('Build'){
            sh 'docker stop $(docker ps -qf "name=autotraderweb") || exit 0'
            sh 'docker-compose rm -v --force'
            sh 'docker-compose build'
        }

        stage('RunServer'){
         sh 'docker-compose up -d'
        }
    }
    catch (err) {
    currentBuild.result = 'FAILURE'
    }
    finally {
        if( currentBuild.result != 'SUCCESS')
        {
            def mailRecipients = "slash.gordon.dev@gmail.com"
            def emailBody = '${SCRIPT, template="regressionfailed.groovy"}'
            def emailSubject = "${env.JOB_NAME} - Build# ${env.BUILD_NUMBER} - ${env.BUILD_STATUS}"
            emailext(mimeType: 'text/html', subject: emailSubject, to: mailRecipients, body: emailBody)
        }
    }
}
