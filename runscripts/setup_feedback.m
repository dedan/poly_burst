data_path = 'c:\Dokumente und Einstellungen\ml\Eigene Dateien\stephan_luis\data\270312_185758\';
pyff('init', 'TrainingFeedback');
pause(1);
pyff('setint', 'n_groups', 2);
pyff('setint', 'group_size', 6);
pyff('setint', 'n_first_polies', 3);
pyff('setint', 'n_bursts', 1);
pyff('set', 'data_path', data_path);

%pyff('load_settings', CENTERSPELLER_file);
%pause(1);
pyff('setint', 'geometry', VP_SCREEN);
