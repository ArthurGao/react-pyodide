import { useEffect, useState } from 'react';
import script from './python/main.py';
import diagram from './python/test.py';
import logo from './logo.svg';
import './App.css';

const runScript = async (code) => {
  if (!('pyodide' in window)) {
      window.pyodide= await window.loadPyodide({
      indexURL : "https://cdn.jsdelivr.net/pyodide/v0.18.1/full/"
    });
    await window.pyodide.loadPackage("pillow");
    await window.pyodide.loadPackage("pandas");
    await window.pyodide.loadPackage("matplotlib");
  }
  return await window.pyodide.runPythonAsync(code);
}

const App = () => {
  const [output, setOutput] = useState("(loading...)");
  const [diagramOut, setDiagramOut] = useState("(loading...)");

  useEffect(() => {
    const run = async () => {
      const scriptText = await (await fetch(script)).text();
      const diagramResult =  await (await fetch(diagram)).text();

      const out = await runScript(scriptText);
      setOutput(out);

      const diagramResOut = await runScript(diagramResult);
      //setDiagramOut(diagramResOut)
      document.getElementById('matplotlib-output').appendChild(diagramResOut)

    }
    run();

  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          5 + 7 = {output}
        </p>
      </header>

      <div id="matplotlib-output" src={diagramOut}></div>

    </div>
  );
}

export default App;
