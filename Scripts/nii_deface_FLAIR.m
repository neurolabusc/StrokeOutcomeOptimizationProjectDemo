function nii_deface_TRACE
%dirs = dirVisible('/Users/chris/SOOP/bids/sub-*');
%dirs = dirVisible('/Volumes/SOOP/soup/sub-*');
dirs = dirVisible('/Users/chris/SOOP/sooper/sub-*');
dirs = dirVisible('/Users/chris/fx/bids/sub-*');
for i = 1 : length(dirs)
    folder = fullfile(dirs(i).folder, dirs(i).name, 'anat');
    flairs = dirVisible(fullfile(folder, '*_FLAIR.nii'));
    if isempty(flairs)
        fprintf('nothing to do')
        continue
    end
    flair = fullfile(flairs(1).folder, flairs(1).name);
    [p,n,x] = fileparts(flair);
    ufnm = fullfile(p, ['_',n,x]);
    if exist(ufnm, 'file')
        continue;
    end
    fprintf('%d/%d = %s\n', i, length(dirs), flair)
    nii_setOrigin12x(flair, 4);
    nii_deface(flair, true);
end

function d=dirVisible(pathFolder)
d = dir(pathFolder);
d = d(arrayfun(@(d) ~strcmp(d.name(1),'.'),d));
%we use underscores for bad files
d = d(arrayfun(@(d) ~strcmp(d.name(1),'_'),d));
%end dirVisible()