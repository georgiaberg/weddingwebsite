/**
 * Receives RSVP submissions and gift-registry claims from the site's
 * appsScriptUrl and logs each to its own tab in the bound Sheet.
 *
 * Setup:
 *   1. Create a Google Sheet, then Extensions > Apps Script, and paste
 *      this file in as Code.gs.
 *   2. Deploy > New deployment > type "Web app".
 *      Execute as: Me. Who has access: Anyone.
 *      (Must be "Anyone" — the site posts with fetch mode "no-cors",
 *      which cannot carry an OAuth/session handshake.)
 *   3. Copy the resulting /exec URL into index.html's appsScriptUrl default.
 *
 * Because the site can't read the response (no-cors), it always shows
 * "sent" / "claimed" optimistically. Test by submitting a real RSVP and
 * checking the Sheet updates.
 */
function doPost(e) {
  var params = e.parameter;
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  if (params.type === "claim") {
    var claims = ss.getSheetByName("Claims") || ss.insertSheet("Claims");
    if (claims.getLastRow() === 0) claims.appendRow(["Gift", "Claimed at"]);
    claims.appendRow([params.gift || "", params.at || new Date().toISOString()]);
  } else {
    var rsvps = ss.getSheetByName("RSVPs") || ss.insertSheet("RSVPs");
    if (rsvps.getLastRow() === 0) {
      rsvps.appendRow(["Name", "Attending", "Guests", "Email", "Dietary", "Song", "Note", "Submitted at"]);
    }
    rsvps.appendRow([
      params.name || "",
      params.attending || "",
      params.guests || "",
      params.email || "",
      params.dietary || "",
      params.song || "",
      params.note || "",
      params.submittedAt || new Date().toISOString()
    ]);
  }

  return ContentService.createTextOutput("ok");
}
