# Most recent images — water-adjacent nodes

The actual JPEG bytes couldn't be downloaded yet: the Sage MCP server's
storage credentials (`plebbyd:...`) are being rejected with `Invalid token`
on every path (proxy URL, direct storage + basic auth). This is a
credentials problem on the server side, not a bug in this folder's setup.

`manifest.csv` has the real, verified metadata pulled from Sage's data
API for each water-adjacent camera node: node ID, location, last-reported
timestamp, and the direct storage URL for the most recent image (where
one exists — some cameras are listed as active hardware but haven't
uploaded in 30+ days).

Once you have a working Sage username/token (e.g. from your own Sage
account), run:

```
SAGE_USER=youruser SAGE_TOKEN=yourtoken ./download.sh
```

This reads `manifest.csv` and saves each image under the filename in the
`filename` column (`node_location_date_time_reporting.jpg`).
