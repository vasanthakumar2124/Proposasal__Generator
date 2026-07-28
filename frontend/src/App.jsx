import './App.css'

import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";


import GenerateProposal from "./pages/GenerateProposal";
import ProposalResult from "./pages/ProposalResult";
import ProposalHistory from "./pages/ProposalHistory";


function App(){

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<GenerateProposal />}
        />


        <Route
          path="/result"
          element={<ProposalResult />}
        />


        <Route
          path="/history"
          element={<ProposalHistory />}
        />

      </Routes>

    </BrowserRouter>

  )

}


export default App;