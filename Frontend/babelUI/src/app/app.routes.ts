import { Routes } from '@angular/router';
import { Homepage } from './components/General/homepage/homepage';
import { AllSeries } from './components/Series/all-series/all-series';
import { SeriesPage } from './components/Series/series-page/series-page';
import { ChapterPage } from './components/Chapters/chapter-page/chapter-page';
import { Discord } from './components/General/discord/discord';
import { Login } from './components/Users/login/login';
import { Register } from './components/Users/register/register';
import { Profile } from './components/Users/profile/profile';
import { Admin } from './components/Admin/admin/admin';
import { AddSeries } from './components/Series/add-series/add-series';
import { EditSeries } from './components/Series/edit-series/edit-series';
import { AddChapter } from './components/Chapters/add-chapter/add-chapter';
import { EditChapter } from './components/Chapters/edit-chapter/edit-chapter';
import { AuthGuard } from './services/auth.guard';
import { TranslatorList } from './components/Admin/translator/translator-list';
import { CreateJob } from './components/Admin/create-job/create-job';
import { JobDetail } from './components/Admin/job-detail/job-detail';
import { JobPreview } from './components/Admin/job-preview/job-preview';

export const routes: Routes = [
  { path: '', component: Homepage },
  { path: 'series', component: AllSeries },
  { path: 'series/:id', component: SeriesPage },
  { path: 'series/:id/chapter/:chapterId', component: ChapterPage },
  { path: 'discord', component: Discord },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'profile', component: Profile },
  { path: 'staff', component: Admin, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/add-series', component: AddSeries, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/edit-series/:id', component: EditSeries, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/add-chapter/:seriesId', component: AddChapter, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/edit-chapter/:id', component: EditChapter, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/translator', component: TranslatorList, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/translator/create', component: CreateJob, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/translator/job/:id', component: JobDetail, canActivate: [AuthGuard], data: { requiresStaff: true } },
  { path: 'staff/translator/preview/:id', component: JobPreview, canActivate: [AuthGuard], data: { requiresStaff: true } }
];
