function nii_deface_TRACE
%dirs = dirVisible('/Users/chris/SOOP/bids/sub-*');
%dirs = dirVisible('/Volumes/SOOP/soup/sub-*');
dirs = dirVisible('/Users/chris/SOOP/sooper/sub-*');
for i = 1 : length(dirs)
    folder = fullfile(dirs(i).folder, dirs(i).name, 'anat');
    traces = dirVisible(fullfile(folder, '*_TRACE.nii'));
    if isempty(traces)
        continue
    end
    trace = fullfile(traces(1).folder, traces(1).name);
    adcs = dirVisible(fullfile(folder, '*_ADC.nii'));
     if isempty(adcs)
        continue
    end
    adc = fullfile(adcs(1).folder, adcs(1).name);
    lesions = dirVisible(fullfile(folder, 'lesion_*.nii'));
    fprintf('%d/%d %d = %s %s\n', i,length(dirs), length(lesions), trace, adc)
    [p,n,x] = fileparts(trace);
    ufnm = fullfile(p, ['_',n,x]);
    if exist(ufnm, 'file')
        continue;
    end
    fnms = {trace};
    fnms{end+1} = fullfile(adc);
    for j = 1: length(lesions)
        fnms{end+1} = fullfile(lesions(j).folder, lesions(j).name);
    end
    nii_setOrigin12x(fnms, 3);
    %do NOT deface lesions!
    fnms = {trace};
    fnms{end+1} = fullfile(adc);
    nii_deface(fnms, true);
end

function d=dirVisible(pathFolder)
d = dir(pathFolder);
d = d(arrayfun(@(d) ~strcmp(d.name(1),'.'),d));
%we use underscores for bad files
d = d(arrayfun(@(d) ~strcmp(d.name(1),'_'),d));
%end dirVisible()