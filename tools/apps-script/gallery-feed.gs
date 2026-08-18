/**
 * Proxies an Airtable table as JSON for the site's galleryFeedUrl, so the
 * Airtable token never has to sit in client-side code.
 *
 * Setup:
 *   1. New standalone Apps Script project (script.google.com > New project).
 *      Paste this file in as Code.gs.
 *   2. Project Settings > Script Properties, add:
 *        AIRTABLE_TOKEN     - a Personal Access Token from
 *                             airtable.com/create/tokens, scoped to
 *                             data.records:read and only this base.
 *        AIRTABLE_BASE_ID   - starts with "app...", from the base's API docs.
 *        AIRTABLE_TABLE     - the table name, e.g. "Photos".
 *   3. Deploy > New deployment > type "Web app".
 *      Execute as: Me. Who has access: Anyone.
 *   4. Copy the resulting /exec URL into index.html's galleryFeedUrl default.
 *
 * Expects an Airtable table with fields Name, Caption, Photo (attachment),
 * and optionally Approved (checkbox) for moderation — guests submit
 * through the airtableFormUrl form, which should leave Approved off the
 * form so only records you've checked appear here.
 */
function doGet(e) {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty("AIRTABLE_TOKEN");
  var baseId = props.getProperty("AIRTABLE_BASE_ID");
  var table = props.getProperty("AIRTABLE_TABLE") || "Photos";

  var url = "https://api.airtable.com/v0/" + baseId + "/" + encodeURIComponent(table) + "?pageSize=100";
  var res = UrlFetchApp.fetch(url, {
    headers: { Authorization: "Bearer " + token }
  });
  var data = JSON.parse(res.getContentText());

  var out = (data.records || [])
    .filter(function (r) {
      return r.fields && r.fields.Photo && r.fields.Photo.length &&
        (r.fields.Approved === undefined || r.fields.Approved === true);
    })
    .map(function (r) {
      return {
        fields: {
          Photo: r.fields.Photo,
          Caption: r.fields.Caption || "",
          Name: r.fields.Name || ""
        }
      };
    });

  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}
