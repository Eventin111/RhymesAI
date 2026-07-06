async function generateRhyme() {
    const promptInput = document.getElementById('promptInput').value;
    const taskIdDiv = document.getElementById('taskId');
    const responseDiv = document.getElementById('response');

    if (!promptInput) {
        responseDiv.innerText = 'Please enter a prompt!';
        return;
    }

    responseDiv.innerText = 'Submitting...';
    taskIdDiv.innerText = '';

    try {
        const response = await fetch('http://localhost:8000/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: promptInput }),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        taskIdDiv.innerText = `Task ID: ${data.task_id}`;
        responseDiv.innerText = 'Processing your request...';

        const checkStatus = async () => {
            try {
                const statusResponse = await fetch(`http://localhost:8000/status/${data.task_id}`);
                if (!statusResponse.ok) {
                    throw new Error(`Status check failed: ${statusResponse.status}`);
                }
                
                const statusData = await statusResponse.json();
                
                if (statusData.status === 'completed') {
                    responseDiv.innerText = statusData.response;
                    return;
                }
                if (statusData.status === 'failed') {
                    responseDiv.innerText = `Error: ${statusData.response}`;
                    return;
                }
                
                responseDiv.innerText = `Status: ${statusData.status}...`;
                setTimeout(checkStatus, 1000);
            } catch (error) {
                responseDiv.innerText = `Status check error: ${error.message}`;
            }
        };

        checkStatus();
    } catch (error) {
        responseDiv.innerText = `Error: ${error.message}`;
    }
}