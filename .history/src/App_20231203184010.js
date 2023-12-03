import { useEffect, useState, useRef } from 'react';
import script from './python/main.py';
import diagram from './python/test.py';
import logo from './logo.svg';
import './App.css';

const runScript = async (code) => {
  if (!('pyodide' in window)) {
      window.pyodide= await window.loadPyodide({
      indexURL : "https://cdn.jsdelivr.net/pyodide/v0.24.1/full"
    });
    await window.pyodide.loadPackage("micropip");
    const micropip = window.pyodide.pyimport("micropip");
    await micropip.install('plotly');

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

      const out = await runScript(scriptText);
      //setOutput(out);

      const diagramResOut = await runScript(diagramResult);
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
