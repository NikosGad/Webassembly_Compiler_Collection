import { Component, OnInit } from '@angular/core';
import { sigma } from 'sigma';

@Component({
  selector: 'app-system-admin-graph',
  templateUrl: './system-admin-graph.component.html',
  styleUrls: ['./system-admin-graph.component.css']
})
export class SystemAdminGraphComponent implements OnInit {
  sigmaJS: any;
  graph = {
    nodes: [
      {id: "n0", label: "A node", x: 0, y: 0, size: 1, color: '#008cc2'},
      {id: "n1", label: "Another node", x: 3, y: 1, size: 1, color: '#008cc2'},
      {id: "n2", label: "And a last one", x: 1, y: 3, size: 1, color: '#E57821'}
    ],
    edges: [
      {id: "e0", source: "n0", target: "n1", color: '#282c34', type: 'line', size: 0.5},
      {id: "e2", source: "n2", target: "n0", color: '#FF0000', type: 'line', size: 2}
    ]
  };
  constructor() { }

  ngOnInit() {
      this.sigmaJS = new sigma({
          graph: this.graph,
          container: 'graph-container',
          settings: {
              defaultNodeColor: '#ff0000'
          }
      });

      for (let node of this.sigmaJS.graph.nodes()) {
          node.size = this.sigmaJS.graph.degree(node.id);
          console.log(node);
      }

      this.sigmaJS.refresh();
  }

  logGraph() {
      console.log("Graph", this.sigmaJS);
      this.sigmaJS.refresh();
  }

}
