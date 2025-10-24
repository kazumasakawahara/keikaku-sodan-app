// ネットワーク図可視化
// D3.js Force-Directed Graphを使用した利用者のネットワーク図作成

let simulation;
let svg, g, link, node, linkLabel;

/**
 * ネットワークグラフを作成
 * @param {Object} data - ノードとエッジのデータ
 */
function createNetworkGraph(data) {
    const width = document.getElementById('network-graph').clientWidth;
    const height = 700;

    // デバッグ: データ構造を確認
    console.log('Nodes:', data.nodes);
    console.log('Edges (original):', data.edges);

    // エッジデータをD3.js形式に変換（from/to → source/target）
    const edges = data.edges.map(edge => ({
        source: edge.from,
        target: edge.to,
        relationship: edge.relationship,
        frequency: edge.frequency,
        start_date: edge.start_date
    }));

    console.log('Edges (converted):', edges);

    // SVG要素の設定
    svg = d3.select('#network-graph')
        .attr('width', width)
        .attr('height', height);

    // ズーム機能
    const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // メイングループ
    g = svg.append('g');

    // Force Simulationの設定
    simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(edges)
            .id(d => d.id)
            .distance(150))
        .force('charge', d3.forceManyBody()
            .strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(50));

    // エッジ（リンク）の描画
    link = g.append('g')
        .selectAll('line')
        .data(edges)
        .enter().append('line')
        .attr('class', 'link');

    // エッジラベルの描画
    linkLabel = g.append('g')
        .selectAll('text')
        .data(edges)
        .enter().append('text')
        .attr('class', 'link-label')
        .attr('text-anchor', 'middle')
        .text(d => d.relationship);

    // ノードグループの作成
    const nodeGroup = g.append('g')
        .selectAll('g')
        .data(data.nodes)
        .enter().append('g')
        .attr('class', d => `node node-${d.type}`)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('mouseover', showTooltip)
        .on('mouseout', hideTooltip);

    // ノード（円）の描画
    nodeGroup.append('circle')
        .attr('r', d => d.type === 'user' ? 30 : 20);

    // ノードラベルの描画
    nodeGroup.append('text')
        .attr('dy', d => d.type === 'user' ? 45 : 35)
        .attr('text-anchor', 'middle')
        .text(d => d.label);

    node = nodeGroup;

    // シミュレーションのティック処理
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        linkLabel
            .attr('x', d => (d.source.x + d.target.x) / 2)
            .attr('y', d => (d.source.y + d.target.y) / 2);

        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });
}

/**
 * ドラッグ開始
 */
function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}

/**
 * ドラッグ中
 */
function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

/**
 * ドラッグ終了
 */
function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
}

/**
 * ツールチップ表示
 */
function showTooltip(event, d) {
    const tooltip = d3.select('#tooltip');
    let content = `<strong>${d.label}</strong><br>`;

    if (d.type === 'user') {
        content += `年齢: ${d.data.age || '不明'}歳<br>`;
        content += `性別: ${d.data.gender || '不明'}<br>`;
        if (d.data.support_level) {
            content += `障害支援区分: ${d.data.support_level}`;
        }
    } else if (d.type === 'service' || d.type === 'medical' || d.type === 'other') {
        content += `種別: ${d.data.organization_type || '不明'}<br>`;
        if (d.data.contact) {
            content += `担当: ${d.data.contact}<br>`;
        }
        if (d.data.phone) {
            content += `電話: ${d.data.phone}<br>`;
        }
        if (d.data.frequency) {
            content += `頻度: ${d.data.frequency}`;
        }
    } else if (d.type === 'guardian') {
        content += `種別: ${d.data.guardian_type || '後見人'}<br>`;
        if (d.data.contact) {
            content += `連絡先: ${d.data.contact}`;
        }
    } else if (d.type === 'staff') {
        content += `役割: ${d.data.role || 'スタッフ'}<br>`;
        if (d.data.email) {
            content += `Email: ${d.data.email}`;
        }
    }

    tooltip
        .html(content)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .style('opacity', 1);
}

/**
 * ツールチップ非表示
 */
function hideTooltip() {
    d3.select('#tooltip').style('opacity', 0);
}

/**
 * PNGとしてエクスポート
 */
function exportNetworkAsPNG() {
    const svgElement = document.getElementById('network-graph');
    const svgData = new XMLSerializer().serializeToString(svgElement);

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    canvas.width = svgElement.clientWidth;
    canvas.height = svgElement.clientHeight;

    img.onload = function() {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        canvas.toBlob(function(blob) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `network_${userId}_${new Date().getTime()}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
}

/**
 * SVGとしてエクスポート
 */
function exportNetworkAsSVG() {
    const svgElement = document.getElementById('network-graph');
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `network_${userId}_${new Date().getTime()}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
