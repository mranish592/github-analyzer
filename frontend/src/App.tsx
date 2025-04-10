// import { useState } from 'react';
import './App.css'
import GitHubAnalyzer from './components/GithubAnalyzer';
function App() {

  // const [show, setShow] = useState(false);
  // const [response, setResponse] = useState("");

  return (
    <>
      {/* <div className="flex flex-col items-center justify-center min-h-svh">
        <UsernameForm show={show} setShow={setShow} setReponse={setResponse}></UsernameForm>
        <AnalyzeResponse show={show} response={response}></AnalyzeResponse>
      </div> */}
      <GitHubAnalyzer />
    </>
  )
}

export default App