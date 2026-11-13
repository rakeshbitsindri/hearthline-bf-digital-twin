"use client";

import { useEffect, useState } from "react";

export default function VisitsPage() {
  const [body, setBody] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const summary =
      (typeof window !== "undefined" && window.__HEARTHLINE_VISIT_SUMMARY__) ||
      `${window.location.origin}/visits/summary`;
    fetch(summary)
      .then((r) => {
        if (!r.ok) throw new Error("summary unavailable");
        return r.json();
      })
      .then(setBody)
      .catch(() => setError("Visit summary is not reachable from this page yet."));
  }, []);

  return (
    <section>
      <h2>Visits by city</h2>
      <p className="muted">{body?.note || "Counts from both public sites. City and country only."}</p>
      {error && <p className="muted">{error}</p>}
      {body && (
        <>
          <p className="run-caption">
            {body.total} visits kept of {body.capacity}
          </p>
          <div className="ix-table-wrap">
            <table className="ix-table">
              <thead>
                <tr>
                  <th>City</th>
                  <th>Visits</th>
                </tr>
              </thead>
              <tbody>
                {(body.cities || []).map((row) => (
                  <tr key={row.place}>
                    <td>{row.place}</td>
                    <td className="ix-num">{row.visits}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h3>Sites</h3>
          <div className="ix-table-wrap">
            <table className="ix-table">
              <thead>
                <tr>
                  <th>Site</th>
                  <th>Visits</th>
                </tr>
              </thead>
              <tbody>
                {(body.sites || []).map((row) => (
                  <tr key={row.site}>
                    <td>{row.site}</td>
                    <td className="ix-num">{row.visits}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
