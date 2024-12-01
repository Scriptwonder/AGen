import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const GraphVisualizer = ({ triplets }) => {
  const svgRef = useRef();

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous renders

    const width = 600;
    const height = 400;

    // Convert triplets into nodes and links
    const nodes = [];
    const links = [];
    triplets.forEach(({ source, relation, target }) => {
      nodes.push({ id: source });
      nodes.push({ id: target });
      links.push({ source, target, relation });
    });

    // Remove duplicate nodes
    const uniqueNodes = Array.from(new Set(nodes.map(d => d.id))).map(id => ({ id }));

    // Create the simulation
    const simulation = d3.forceSimulation(uniqueNodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Add links (edges)
    const link = svg.append('g')
      .attr('stroke', '#aaa')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke-width', 2);

    // Add nodes (circles)
    const node = svg.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(uniqueNodes)
      .join('circle')
      .attr('r', 10)
      .attr('fill', '#69b3a2')
      .call(drag(simulation));

    // Add text labels for nodes
    const labels = svg.append('g')
      .selectAll('text')
      .data(uniqueNodes)
      .join('text')
      .attr('dx', 12)
      .attr('dy', 4)
      .text(d => d.id);

    // Add relation labels on links
    const linkLabels = svg.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .attr('class', 'relation-label')
      .text(d => d.relation);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      labels
        .attr('x', d => d.x)
        .attr('y', d => d.y);

      linkLabels
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2);
    });

    // Add drag behavior to nodes
    function drag(simulation) {
      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }

      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }

      return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }
  }, [triplets]);

  return <svg ref={svgRef} width={600} height={400}></svg>;
};

export default GraphVisualizer;
