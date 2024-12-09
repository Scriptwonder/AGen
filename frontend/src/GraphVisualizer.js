import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const GraphVisualizer = ({ triplets }) => {
  const svgRef = useRef();

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous renders

    // Define a marker for arrows
    svg.append("defs")
    .append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "-0 -5 10 10")
    .attr("refX", 25) // Adjust the position of the arrow
    .attr("refY", 0)
    .attr("orient", "auto")
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("xoverflow", "visible")
    .append("svg:path")
    .attr("d", "M 0,-5 L 10 ,0 L 0,5")
    .attr("fill", "#aaa")
    .style("stroke", "none");

    const width = window.innerWidth;
    const height = window.innerHeight * 0.8;

    svg.attr('viewBox', [0, 0, width, height])
      .attr('preserveAspectRatio', 'xMidYMid meet');

    // Create the main group that we will zoom and pan
    const mainGroup = svg.append("g");

    // Set up zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 2]) // Allow zoom from 10% to 500%
      .on("zoom", (event) => {
        mainGroup.attr("transform", event.transform);
      });

    svg.call(zoom);
    //svg.call(zoom).call(zoom.transform, d3.zoomIdentity.translate(width / 4, height / 4).scale(0.75));

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
      .force('link', d3.forceLink(links).id(d => d.id).distance(200))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(30));

    simulation.nodes(uniqueNodes);
    simulation.force('link').links(links);

    // Add links (edges)
    const link = mainGroup.append("g")
      .attr("stroke", "#aaa")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 2)
      .attr("marker-end", "url(#arrowhead)"); // Add arrow marker

    // Add nodes (circles)
    const node = mainGroup.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(uniqueNodes)
      .join('circle')
      .attr('r', 10)
      .attr('fill', '#69b3a2')
      .call(drag(simulation));

    // Add text labels for nodes
    const labels = mainGroup.append('g')
      .selectAll('text')
      .data(uniqueNodes)
      .join('text')
      .attr('dx', 12)
      .attr('dy', 4)
      .text(d => d.id);

    // Add relation labels on links
    const linkLabels = mainGroup.append('g')
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

    // Handle window resize
    const resizeHandler = () => {
      const newWidth = window.innerWidth;
      const newHeight = window.innerHeight * 0.8;
      svg.attr('viewBox', [0, 0, newWidth, newHeight]);
      simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
      simulation.alpha(1).restart();
    };

    window.addEventListener('resize', resizeHandler);

    // Cleanup on unmount
    return () => {
      window.removeEventListener('resize', resizeHandler);
    };
  }, [triplets]);

  return <svg ref={svgRef} width="100%" height="80vh" style={{ border: '1px solid black', margin: '20px auto', display: 'block' }}></svg>;
};

export default GraphVisualizer;
