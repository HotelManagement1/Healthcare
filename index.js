document.getElementById('prediction-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const symptom1 = document.getElementById('symptom1').value;
    const symptom2 = document.getElementById('symptom2').value;
    const symptom3 = document.getElementById('symptom3').value;

    const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptom1, symptom2, symptom3 })
    });

    const result = await response.json();
    document.getElementById('result').textContent = `Prediction: ${result.disease}`;
});
