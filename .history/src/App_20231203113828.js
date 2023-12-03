import { useEffect, useState } from 'react';
import script from './python/main.py';
import diagram from './python/test.py';
import logo from './logo.svg';
import './App.css';

const runScript = async (code) => {
  const pyodide = await window.loadPyodide({
    indexURL : "https://cdn.jsdelivr.net/pyodide/v0.18.1/full/"
  });

  return await pyodide.runPythonAsync(code);
}

const App = () => {
  const [output, setOutput] = useState("(loading...)");

  useEffect(() => {
    const run = async () => {
      const scriptText = await (await fetch(script)).text();
      const diagramResult =  await (await fetch(diagram));
      document.getElementById("pyplotfigure").src=diagramResult

      const out = await runScript(scriptText);
      setOutput(out);
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

      <div id="matplotlib-output"></div>

    </div>
  );
}

export default App;
