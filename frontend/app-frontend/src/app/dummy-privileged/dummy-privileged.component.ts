import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-dummy-privileged',
  templateUrl: './dummy-privileged.component.html',
  styleUrls: ['./dummy-privileged.component.css']
})
export class DummyPrivilegedComponent implements OnInit {
  info: string;
  constructor(private http: HttpClient) { }

  ngOnInit() {
  }

  getPrivInfo() {
    const formData = new FormData();

    this.http.post('http://127.0.0.1:8080/api/priv', formData).subscribe(
      (res:any) => {
        this.info = res.message;
      }
    );
  }

}
