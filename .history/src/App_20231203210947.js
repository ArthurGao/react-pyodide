import { useEffect, useState, useRef } from 'react';
import script from './python/main.py';
import diagram from './python/test.py';
import './App.css';

const runScript = async (code) => {
  if (!('pyodide' in window)) {
      window.pyodide= await window.loadPyodide();
    await window.pyodide.loadPackage("micropip");
    const micropip = window.pyodide.pyimport("micropip");
    await micropip.install('plotly');
    await micropip.install('nolds');
    await micropip.install('requests');
    await micropip.install('ssl');
    

    await window.pyodide.loadPackage("pillow");
    await window.pyodide.loadPackage("pandas");
    await window.pyodide.loadPackage("matplotlib");

  }
  return await window.pyodide.runPythonAsync(code);
}

const App = () => {
  const [output, setOutput] = useState("(loading...)");
  const [diagramOut, setDiagramOut] = useState("(loading...)");
  const matplotlibOutputRef = useRef(null);

  useEffect(() => {
    const run = async () => {
      const scriptText = await (await fetch(script)).text();
      const diagramResult =  await (await fetch(diagram)).text();

      //const out = await runScript(scriptText);
      //setOutput(out);

      // Define the URL
      const url = "https://nicoforecasting.azurewebsites.net/api/forecast/070f528c-2f8a-4399-a599-cfb71faee319/746b5af1-ea1f-4081-b3f0-d48abd7313a1?code=hwDugEQ9K71-rA_RbADAsjMZwM_d9KeX1auHpm-odUj7AzFug_qugw==";

      // Define headers with Content-Type
      const headers = {
        "Content-Type": "application/csv"
      };
      let result;
      // Make the GET request using fetch
      fetch(url, {
        method: "GET",
        headers: headers
      })
        .then(response => {
          if (response.status === 200) {
            return response.text();
          } else {
            throw new Error(`Request failed with status code ${response.status}`);
          }
        })
        .then(content => {
          // Handle the response content here
          result = content.replace(/"/g, '');
        })
        .catch(error => {
          // Handle any errors that occurred during the request
          console.error("Request Error:", error);
        });


      //const diagramResOut = await runScript(diagramResult);
      const out = await window.pyodide.runPythonAsync(scriptText, window.pyodide.toPy(
        {"content": result}));
      const imgElement = document.createElement('img');
      //imgElement.src = `data:image/png;base64,${diagramResOut}`;
      imgElement.src = `data:image/png;base64,${out}`;
      matplotlibOutputRef.current.appendChild(imgElement);


    }
    run();

  }, []);

  return (
    <div className="App">
      <div ref={matplotlibOutputRef}></div>
    </div>
  );
}

export default App;
