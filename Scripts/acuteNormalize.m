function acuteNormalize
% This script normalizes FLAIR scans and lesions
% It assumes lesions are drawn on a TRACE scan and a FLAIR is present
% the TRACE is coregistered to the FLAIR, the FLAIR is normalized
% BSD 2-Clause license Chris Rorden 12/2023

dirs = dirVisible('/path/to/bids');
outdir = pwd; //e.g. '/Users/chris/soup/norm';
%dirs = dirVisible('/Users/chris/SOOP/sooper');
for i = 1 : length(dirs)
    d = fullfile(dirs(i).folder, dirs(i).name, 'anat', '*FLAIR.nii');
    fprintf('%d/%d %s\n', i,length(dirs), d)
    niis = dirVisible(d);
    [~,idx] = sort(string({niis.name}),2,'ascend');
    for j=idx
        fl = fullfile(niis(j).folder, niis(j).name);
        [p,n,x] = fileparts(fl);
        subj = split(n,'_');
        subj = subj{1};
        les = fullfile(niis(j).folder, 'lesion_total.nii');
        les2 = [];
        tr2 = [];
        if exist(les, 'file')
            tr = fullfile(niis(j).folder, [subj, '_TRACE.nii']);
            if ~exist(tr, 'file')
                error('Unable to find %s\n', tr)
            end
            les2 = fullfile(outdir, [subj, '_lesion.nii']);
            tr2 = fullfile(outdir, [subj, '_TRACE.nii']);
            copyfile(les,les2);
            copyfile(tr,tr2);
        end

        fl2 = fullfile(outdir, [subj, '_FLAIR.nii']); 
        copyfile(fl,fl2);
        normalizeFlair(fl2, les2, tr2);
        deletenii(fl2);
        deletenii(les2);
        deletenii(tr2);
    end
end
%end acuteNormalize()

function deletenii(fnm)
if ~isempty(fnm) && exist(fnm, 'file')
    delete(fnm)
end
%end deletenii()

function normalizeFlair(fl, les, tr)
matlabbatch{1}.spm.tools.MRI.MRnorm.anat = {fl};
matlabbatch{1}.spm.tools.MRI.MRnorm.les = {les};
matlabbatch{1}.spm.tools.MRI.MRnorm.t2 = {tr};
matlabbatch{1}.spm.tools.MRI.MRnorm.modality = 3;
matlabbatch{1}.spm.tools.MRI.MRnorm.brainmask = 0;
%matlabbatch{1}.spm.tools.MRI.MRnorm.bb = [-78 -112 -50; 78 76 85];
matlabbatch{1}.spm.tools.MRI.MRnorm.bb = [NaN NaN NaN; NaN NaN NaN];
matlabbatch{1}.spm.tools.MRI.MRnorm.vox = [1 1 1];
matlabbatch{1}.spm.tools.MRI.MRnorm.DelIntermediate = 1;
matlabbatch{1}.spm.tools.MRI.MRnorm.AutoSetOrigin = 0;
spm_jobman('run',matlabbatch);
%end normalizeFlair()

function d=dirVisible(pathFolder)
d = dir(pathFolder);
d = d(arrayfun(@(d) ~strcmp(d.name(1),'.'),d));
%we use underscores for bad files
d = d(arrayfun(@(d) ~strcmp(d.name(1),'_'),d));
%end dirVisible()