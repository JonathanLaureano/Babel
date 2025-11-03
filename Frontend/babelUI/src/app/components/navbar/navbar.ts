import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { SearchComponent } from '../search/search';

@Component({
  selector: 'app-navbar',
  imports: [CommonModule, RouterLink, RouterLinkActive, SearchComponent],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar {}
