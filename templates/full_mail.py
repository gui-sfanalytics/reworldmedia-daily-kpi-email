def build_mail_html(report_date, image_sources=None):
    """
    image_sources permet d'utiliser :
    - en local : des cid Gmail
    - en GCP : des URLs GCS signées
    """

    default_sources = {
        "daily_kpi_web": "cid:daily_web",
        "daily_performance_indicators": "cid:daily_performance",
        "daily_top_subscriptions": "cid:daily_top_subscriptions",

        "mtd_kpi_web": "cid:mtd_web",
        "mtd_performance_indicators": "cid:mtd_performance",
        "mtd_top_subscriptions": "cid:mtd_top_subscriptions",

        "ytd_kpi_web": "cid:ytd_web",
        "ytd_performance_indicators": "cid:ytd_performance",
        "ytd_top_subscriptions": "cid:ytd_top_subscriptions",

        "subscription_charts": "cid:subscription_charts",
    }

    if image_sources:
        default_sources.update(image_sources)

    img = default_sources

    def image_row(src, width=760, padding_bottom=0):
        return f"""
        <tr>
          <td align="center" bgcolor="#f2f2f2" style="padding:0 0 {padding_bottom}px 0; background-color:#f2f2f2;">
            <img
              src="{src}"
              width="{width}"
              style="display:block; width:{width}px; max-width:{width}px; height:auto; margin:0 auto; border:0; outline:none; text-decoration:none;"
              border="0"
              alt=""
            />
          </td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Reporting Quotidien ReworldMedia</title>
</head>

<body bgcolor="#f2f2f2" style="margin:0; padding:0; background-color:#f2f2f2;">

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f2f2f2" style="width:100%; background-color:#f2f2f2; border-collapse:collapse; margin:0; padding:0;">
    <tr>
      <td align="center" bgcolor="#f2f2f2" style="padding:24px 0; background-color:#f2f2f2;">

        <table role="presentation" width="760" cellpadding="0" cellspacing="0" border="0" bgcolor="#f2f2f2" style="width:760px; max-width:760px; background-color:#f2f2f2; border-collapse:collapse; margin:0 auto;">

          <tr>
            <td align="center" bgcolor="#f2f2f2" style="padding:0 0 34px 0; background-color:#f2f2f2;">
              <table role="presentation" width="760" cellpadding="0" cellspacing="0" border="0" style="width:760px; background-color:#000000; border-collapse:collapse;">
                <tr>
                  <td height="40" style="height:40px; line-height:40px; font-size:1px; background-color:#000000;">
                    &nbsp;
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td bgcolor="#f2f2f2" style="font-family:Georgia, serif; font-size:18px; color:#000000; line-height:28px; padding:0 0 28px 0; background-color:#f2f2f2;">
              Bonjour,<br>
              voici votre rapport du <strong>{report_date}</strong> pour Reworld Media.
            </td>
          </tr>

          {image_row(img["daily_performance_indicators"])}
          {image_row(img["daily_top_subscriptions"], padding_bottom=24)}

          {image_row(img["mtd_kpi_web"])}
          {image_row(img["mtd_performance_indicators"])}
          {image_row(img["mtd_top_subscriptions"], padding_bottom=24)}

          {image_row(img["ytd_kpi_web"])}
          {image_row(img["ytd_performance_indicators"])}
          {image_row(img["ytd_top_subscriptions"], padding_bottom=24)}

          {image_row(img["subscription_charts"], width=720)}

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""

    return html
