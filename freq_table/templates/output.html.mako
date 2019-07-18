## -*- coding: utf-8 -*-

<!DOCTYPE html>
<html lang="ru-RU">
<head>
    <meta charset="utf-8">
    <link href="style.css" rel="stylesheet" type="text/css">
</head>

<body>
% for page in data:
    <div class="page-container">
        <div class="flex-container">
        % for slice in page:
            <div class="flex-item">
                ${gen_table(slice)}
            </div>
        % endfor
        </div>

        <p class="footer">
            ${page.footer}
        </footer>
    </div>
% endfor
</body>

<%def name="gen_table(slice)">
    <table>
        <caption>
            ${slice.caption}
        </caption>
        <thead>
            <tr>
            % for col in table_columns:
                <th class="${col.get('class', '')}" style="width: ${col.get('width', 'initial')};">
                    <p class="primary">
                        ${col['primary_header']}
                    </p>
                    % if 'secondary_header' in col:
                        <p class="secondary">
                            ${col['secondary_header']}
                        </p>
                    % endif
                </th>
            % endfor
            </tr>
        </thead>

        <tbody>
        % for row in slice:
            <tr>
            % for col in table_columns:
                <td class="${col.get('class', '')}">
                    <p class="primary">
                        ${row[col['primary_attr']] | h}
                    </p>
                    % if 'secondary_attr' in col:
                        <p class="secondary">
                            ${row[col['secondary_attr']] | h}
                        </p>
                    % endif
                </td>
            % endfor
            </tr>
        % endfor
        </tbody>
    </table>
</%def>
