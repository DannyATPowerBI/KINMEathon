/* Prepared visualization for the exercise. Reads calculated KNIME input rows. */
(function () {
    'use strict';
    const host = document.createElement('main');
    document.body.replaceChildren(host);
    function element(tag, text, parent, className) {
        const el = document.createElement(tag);
        if (text !== undefined) el.textContent = text;
        if (className) el.className = className;
        (parent || host).appendChild(el);
        return el;
    }
    element('div', 'FRANKENWERK · FERTIGUNGSPLANUNG', host, 'eyebrow');
    element('h1', 'Unsere nächste Schicht');
    element('p', 'Synthetischer Montageplan · Schichtbeginn 06:00 · drei gleichwertige Montagezellen', host, 'subtitle');
    const required = ['Auftrag_ID', 'Produkt', 'Maschine_ID', 'Maschine', 'Start_Min', 'Ende_Min', 'Dauer_Min', 'Schicht_Min'];
    const cols = typeof knimeDataTable !== 'undefined' && knimeDataTable ? knimeDataTable.getColumnNames() : [];
    const missing = required.filter(c => !cols.includes(c));
    if (missing.length) {
        element('h2', 'Die Plantafel wartet auf euren Plan.');
        element('p', 'Berechnet Dauer und Endzeit, ergänzt den Maschinenstamm und verbindet die fertige Plantabelle mit diesem Node.');
        element('p', 'Noch benötigte Spalten: ' + missing.join(', '));
        return;
    }
    const jobs = knimeDataTable.getRows().map(row => Object.fromEntries(cols.map((c, i) => [c, row.data[i]])));
    const invalid = jobs.some(j => !j.Auftrag_ID || !j.Maschine_ID || !j.Maschine ||
        ['Start_Min', 'Ende_Min', 'Dauer_Min', 'Schicht_Min'].some(c => typeof j[c] !== 'number' || !Number.isFinite(j[c])) ||
        j.Start_Min < 0 || j.Dauer_Min <= 0 || j.Ende_Min <= j.Start_Min || j.Schicht_Min <= 0 ||
        Math.abs(j.Ende_Min - j.Start_Min - j.Dauer_Min) > 0.0001);
    if (!jobs.length || invalid || new Set(jobs.map(j => j.Auftrag_ID)).size !== jobs.length) {
        element('h2', 'Bitte die Plandaten prüfen.');
        element('p', 'Aufträge brauchen eindeutige IDs, vollständige Zeitwerte und eine positive Dauer. Ende muss Start plus Dauer ergeben.');
        return;
    }
    const machines = [...new Set(jobs.map(j => j.Maschine_ID))].sort();
    const colors = ['#087f8c', '#7057b5', '#b96824'];
    const cards = element('section', undefined, host, 'cards');
    machines.forEach((id, index) => {
        const own = jobs.filter(j => j.Maschine_ID === id);
        const shift = own[0].Schicht_Min;
        if (own.some(j => j.Schicht_Min !== shift || j.Maschine !== own[0].Maschine)) {
            throw new Error('Uneinheitlicher Maschinenstamm: ' + id);
        }
        const minutes = own.reduce((n, j) => n + j.Dauer_Min, 0);
        const card = element('article', undefined, cards, 'card');
        card.style.borderTopColor = colors[index % colors.length];
        element('h2', own[0].Maschine, card);
        element('strong', minutes + ' min', card);
        element('p', (minutes / shift * 100).toLocaleString('de-DE', {maximumFractionDigits: 1}) + ' % Arbeitslast · ' + own.length + ' Aufträge', card);
    });
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    const W = 1280, H = 410, left = 150, top = 90, plotWidth = 1070;
    const horizon = Math.max(540, Math.ceil(Math.max(...jobs.map(j => j.Ende_Min)) / 60) * 60);
    const x = min => left + min / horizon * plotWidth;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('xmlns', NS);
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'Gantt-Diagramm: Aufträge je Montagezelle über der Uhrzeit');
    element('div', undefined, host, 'chart').appendChild(svg);
    function shape(tag, attrs, text) {
        const n = document.createElementNS(NS, tag);
        Object.entries(attrs).forEach(([key, v]) => n.setAttribute(key, v));
        if (text !== undefined) n.textContent = text;
        svg.appendChild(n);
        return n;
    }
    function time(min) {
        const total = Math.round(360 + min);
        return String(Math.floor(total / 60)).padStart(2, '0') + ':' + String(total % 60).padStart(2, '0');
    }
    shape('rect', {width: W, height: H, fill: '#fff'});
    shape('text', {x: 24, y: 30, fill: '#183746', 'font-size': 20, 'font-family': 'Arial'}, 'Schichtplan · FrankenWerk');
    shape('text', {x: 24, y: 55, fill: '#567', 'font-size': 13, 'font-family': 'Arial'}, 'Alle Werte synthetisch · Balken enthalten Rüsten und Bearbeitung');
    for (let min = 0; min <= horizon; min += 60) {
        shape('line', {x1: x(min), x2: x(min), y1: top - 10, y2: 345, stroke: '#dbe5e9'});
        shape('text', {x: x(min), y: top - 20, fill: '#456', 'font-size': 12, 'font-family': 'Arial', 'text-anchor': 'middle'}, time(min));
    }
    let overlaps = 0;
    machines.forEach((id, index) => {
        const own = jobs.filter(j => j.Maschine_ID === id).sort((a, b) => a.Start_Min - b.Start_Min);
        const shift = own[0].Schicht_Min, y = top + index * 86;
        shape('rect', {x: left, y, width: plotWidth, height: 58, fill: '#f3f7f8', rx: 6});
        if (shift < horizon) shape('rect', {x: x(shift), y, width: x(horizon) - x(shift), height: 58, fill: '#fff0e9'});
        shape('text', {x: 24, y: y + 32, fill: '#183746', 'font-size': 14, 'font-family': 'Arial'}, own[0].Maschine);
        const shiftLine = shape('line', {x1: x(shift), x2: x(shift), y1: y - 5, y2: y + 63, stroke: '#c34630', 'stroke-dasharray': '5 4', 'stroke-width': 2});
        shiftLine.dataset.shiftEnd = shift;
        own.forEach(job => {
            const conflict = own.some(other => other !== job && other.Start_Min < job.Ende_Min && other.Ende_Min > job.Start_Min);
            if (conflict) overlaps++;
            const rect = shape('rect', {x: x(job.Start_Min), y: y + 7, width: x(job.Ende_Min) - x(job.Start_Min), height: 44, rx: 5,
                fill: colors[index % colors.length], stroke: conflict ? '#b3261e' : 'none', 'stroke-width': 4});
            rect.dataset.job = job.Auftrag_ID;
            const title = document.createElementNS(NS, 'title');
            title.textContent = job.Auftrag_ID + ' · ' + job.Produkt + ' · ' + time(job.Start_Min) + '–' + time(job.Ende_Min) + ' · ' + job.Dauer_Min + ' min';
            rect.appendChild(title);
            shape('text', {x: x(job.Start_Min) + 7, y: y + 26, fill: '#fff', 'font-size': 12, 'font-family': 'Arial', 'pointer-events': 'none'}, job.Auftrag_ID);
            if (job.Dauer_Min >= 65) shape('text', {x: x(job.Start_Min) + 7, y: y + 42, fill: '#fff', 'font-size': 10, 'font-family': 'Arial', 'pointer-events': 'none'}, time(job.Start_Min) + '–' + time(job.Ende_Min));
        });
    });
    const late = jobs.filter(j => j.Ende_Min > j.Schicht_Min).length;
    shape('text', {x: 24, y: 385, fill: '#567', 'font-size': 12, 'font-family': 'Arial'}, 'Gestrichelt: Schichtende · heller Hintergrund: Zeit danach · rote Kontur: zeitliche Überschneidung');
    element('p', jobs.length + ' Aufträge · ' + late + ' nach Schichtende · ' + overlaps + ' mit zeitlicher Überschneidung', host, 'summary');
    element('p', 'Arbeitslast = gesamte Auftragsdauer / Schichtkapazität. Sie umfasst auch Zeit nach Schichtende. Freie Lücken und Terminkonflikte sind in der Zeitachse sichtbar.', host, 'note');
    const actions = element('div', undefined, host, 'actions');
    function download(name, type, content) {
        const url = URL.createObjectURL(new Blob([content], {type}));
        const a = document.createElement('a'); a.href = url; a.download = name; a.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
    element('button', 'Plantafel als SVG speichern', actions).onclick = () => {
        download('FrankenWerk_Schichtplan.svg', 'image/svg+xml;charset=utf-8', new XMLSerializer().serializeToString(svg));
    };
    element('button', 'Plan als HTML speichern', actions).onclick = () => {
        const clone = host.cloneNode(true); clone.querySelector('.actions').remove();
        const css = Array.from(document.querySelectorAll('style')).map(s => s.textContent).join('\n');
        download('FrankenWerk_Schichtplan.html', 'text/html;charset=utf-8', '<!doctype html><html lang="de"><meta charset="utf-8"><title>FrankenWerk Schichtplan</title><style>' + css + '</style><body>' + clone.outerHTML + '</body></html>');
    };
})();
