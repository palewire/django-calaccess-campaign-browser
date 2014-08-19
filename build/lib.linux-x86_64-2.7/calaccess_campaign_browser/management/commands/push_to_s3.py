import os
import fnmatch
from django.conf import settings
from optparse import make_option
from zipfile import ZipFile, ZIP_DEFLATED
from django.core.management.base import BaseCommand
from django.core.files.base import File
from calaccess_campaign_browser.models import FlatFile

custom_options = (
    make_option(
        "--skip-contributions",
        action="store_false",
        dest="contributions",
        default=True,
        help="Skip contributions zip"
    ),
    make_option(
        "--skip-expenditures",
        action="store_false",
        dest="expenditures",
        default=True,
        help="Skip expenditures zip"
    ),
    make_option(
        "--skip-summary",
        action="store_false",
        dest="summary",
        default=True,
        help="Skip summary zip"
    ),
    make_option(
        "--skip-bulk-download",
        action="store_false",
        dest="create_bulk_download",
        default=True,
        help="Skip campaign_finance bulk zip"
    ),
)


def listdir_fullpath(d):
    """
    Like listdir() but with the full path
    """
    return [os.path.join(d, f) for f in os.listdir(d)]


def all_files(root, patterns='*', single_level=False, yield_folders=False):
    # Expand patterns form semicolon-separated string to list
    # example usage: thefiles = list(all_files('/tmp', '*.py;*.htm;*.html'))
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break


class Command(BaseCommand):
    help = 'Take flatfiles from export_campaign_finance and send em to S3'
    option_list = BaseCommand.option_list + custom_options

    def set_options(self, *args, **kwargs):
        self.data_dir = os.path.join(
            settings.BASE_DIR, 'data')
        os.path.exists(self.data_dir) or os.mkdir(self.data_dir)

        self.zip_dir = os.path.join(
            self.data_dir, 'zip')
        os.path.exists(self.zip_dir) or os.mkdir(self.zip_dir)

    def handle(self, *args, **options):
        self.set_options(*args, **options)
        if options['contributions']:
            self.contributions()

        if options['expenditures']:
            self.expenditures()

        if options['summary']:
            self.summary()

        if options['create_bulk_download']:
            self.create_bulk_download()

    def contributions(self):
        file_path = os.path.join(self.data_dir, 'contributions.csv')
        get_zip = self.zip_this_file(file_path)
        self.load_model(get_zip)

    def expenditures(self):
        file_path = os.path.join(self.data_dir, 'expenditures.csv')
        get_zip = self.zip_this_file(file_path)
        self.load_model(get_zip)

    def summary(self):
        file_path = os.path.join(self.data_dir, 'summary.csv')
        get_zip = self.zip_this_file(file_path)
        self.load_model(get_zip)

    def create_bulk_download(self):
        full_path_list = listdir_fullpath(self.data_dir)
        full_path_list.remove(os.path.join(self.data_dir, 'zip'))

        zip_subdir = 'bulk_campaign_finance'
        zip_file_name = '%s.zip' % os.path.join(
            self.data_dir, 'zip', zip_subdir
        )

        print "attempting to create bulk zip"
        with ZipFile(zip_file_name, 'w', ZIP_DEFLATED) as myzip:
            for file_path in full_path_list:
                file_dir, file_name = os.path.split(file_path)
                zip_path = os.path.join(zip_subdir, file_name)
                # debugger()
                myzip.write(file_path, zip_path)

        print "bulk zip created"
        self.load_model(zip_file_name)

    def load_model(self, file_path):
        """
        Grab the .zip file, create a django model representation
        and push the .zip to S3
        """
        file_name = os.path.split(file_path)[1]

        obj, created = FlatFile.objects.get_or_create(
            file_name=file_name
        )

        try:
            print "Attempting to save", file_name
            obj.s3_file.save(file_path, File(open(file_path)), save=True)
            obj.save()
            print "saved", file_name

        except Exception, e:
            raise e

    def zip_this_file(self, file_path):
        """
        Zip a file and return the path
        """
        # Grab the file name from the path
        csv_name = os.path.split(file_path)[1]
        zip_name = os.path.join(self.zip_dir,  (csv_name + '.zip'))

        print "zipping", csv_name

        with ZipFile(zip_name, 'w', ZIP_DEFLATED) as myzip:
            myzip.write(file_path)

        return zip_name
