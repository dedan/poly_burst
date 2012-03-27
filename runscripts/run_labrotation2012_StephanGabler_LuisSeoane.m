RUN_END = {'S255'};

%pyff('startup','a',[BCI_DIR 'python\pyff\src\Feedbacks'], 'bvplugin', 0);
pyff('startup','a',['C:\Dokumente und Einstellungen\ml\steph_luis'], 'bvplugin', 0);
fprintf('Starting Pyff...\n'); pause(10);

feedback = 'TrainingFeedback';
msg= ['to start ' feedback ' '];

%% Calibration
stimutil_waitForInput('msg_next', [msg 'calibration']);
setup_feedback
%pyff('set', ... % settings for calibration
pyff('save_settings', feedback);
pyff('play', 'basename', ['calibration_' feedback], 'impedances', 0);
stimutil_waitForMarker(RUN_END);
pyff('quit');

%% Train the classifier
bbci.calibrate.file= strcat('calibration_*');
bbci.calibrate.save.file= strcat('bbci_classifier_', feedback, VP_CODE);
[bbci, data]= bbci_calibrate(bbci);
bbci= copy_subfields(bbci, bbci_default);
bbci_save(bbci, data);

%% Free application
stimutil_waitForInput('msg_next', [msg 'free appplication']);
setup_feedback
pyff('set', ... % settings for free application
pyff('play', 'basename', ['free_' feedback], 'impedances', 0);
pause(1)
bbci_apply(bbci);
%% To stop the recording: type 'ppTrigger(255)' in a second Matlab
fprintf('Free-spelling run finished.\n')
pyff('quit');

%% Copy task
stimutil_waitForInput('msg_next', [msg 'copy-task']);
setup_feedback;
pyff('set', ... % settings for copy-task
pyff('play', 'basename', ['copy_' feedback], 'impedances',0);
bbci_apply(bbci);
fprintf('Copy-spelling run finished.\n')
pyff('quit');
