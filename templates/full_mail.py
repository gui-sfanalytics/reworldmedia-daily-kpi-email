def build_mail_html(report_date):
    html = f"""
        <!DOCTYPE html>
        <html>
        <body bgcolor="#f2f2f2" style="margin:0; padding:0; background-color:#f2f2f2;">

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f2f2f2">
        <tr>
        <td align="center" bgcolor="#f2f2f2" style="padding:24px 0;">

        <table role="presentation" width="760" cellpadding="0" cellspacing="0" border="0" bgcolor="#f2f2f2">

        <tr>
        <td>
        <div style="
            width:760px;
            height:40px;
            background:#000;
            margin:0 auto 34px auto;
        "></div>
        </td>
        </tr>

        <tr>
        <td style="
            width:760px;
            font-family:Georgia, serif;
            font-size:18px;
            color:#000;
            line-height:28px;
            padding:0 0 28px 0;
        ">
        Bonjour,<br>
        voici votre rapport du <strong>{report_date}</strong> pour Reworld Media.
        </td>
        </tr>

        <tr><td><img src="cid:daily_performance" width="760" style="display:block; border:0;"></td></tr>

        <tr><td><img src="cid:daily_top_subscriptions" width="760" style="display:block; border:0;"></td></tr>
        <tr><td height="24">&nbsp;</td></tr>

        <tr><td><img src="cid:mtd_web" width="760" style="display:block; border:0;"></td></tr>

        <tr><td><img src="cid:mtd_performance" width="760" style="display:block; border:0;"></td></tr>
        <tr><td><img src="cid:mtd_top_subscriptions" width="760" style="display:block; border:0;"></td></tr>
        <tr><td height="24">&nbsp;</td></tr>

        <tr><td><img src="cid:ytd_web" width="760" style="display:block; border:0;"></td></tr>

        <tr><td><img src="cid:ytd_performance" width="760" style="display:block; border:0;"></td></tr

        <tr><td><img src="cid:ytd_top_subscriptions" width="760" style="display:block; border:0;"></td></tr>

        <tr>
        <td>
            <img src="cid:subscription_charts" style="display:block; margin:0 auto; width:720px;" />
        </td>
        </tr>

        </table>

        </td>
        </tr>
        </table>

        </body>
        </html>
        """
    return html