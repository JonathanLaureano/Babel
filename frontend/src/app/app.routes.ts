import { Routes } from '@angular/router';
import { NovelListComponent } from './components/novel-list/novel-list.component';
import { NovelDetailComponent } from './components/novel-detail/novel-detail.component';

export const routes: Routes = [
  { path: '', component: NovelListComponent },
  { path: 'novel/:id', component: NovelDetailComponent },
  { path: '**', redirectTo: '' }
];

