import json

import pytest
from click.testing import CliRunner

from verta import Client
from verta._cli import cli
from verta._registry import RegisteredModel
import os


class TestCreate:
    def test_create_model(self):
        model_name = RegisteredModel._generate_default_name()

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodel', model_name, '-l', 'label1', '-l', 'label2'],
        )

        assert not result.exception

        result = runner.invoke(
            cli,
            ['registry', 'get', 'registeredmodel', model_name],
        )

        assert not result.exception
        assert "name: \"{}\"".format(model_name) in result.output

    def test_create_version(self, registered_model):
        model_name = registered_model.name
        version_name = "my version"

        filename = "tiny1.bin"
        FILE_CONTENTS = os.urandom(2**16)
        with open(filename, 'wb') as f:
            f.write(FILE_CONTENTS)

        classifier_name = "tiny2.pth"
        CLASSIFIER_CONTENTS = os.urandom(2**16)
        with open(classifier_name, 'wb') as f:
            f.write(CLASSIFIER_CONTENTS)


        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, '-l', 'label1', '-l', 'label2', "--artifact", "file", filename, "--model", classifier_name],
        )
        os.remove(filename)
        os.remove(classifier_name)
        assert not result.exception

        model_version = registered_model.get_version(name=version_name)
        assert model_version.name in result.output
        assert model_version.get_artifact("file").getvalue() == FILE_CONTENTS
        assert model_version.get_labels() == ["label1", "label2"]
        assert model_version.get_model().getvalue() == CLASSIFIER_CONTENTS

    def test_create_version_invalid_key(self, registered_model):
        model_name = registered_model.name
        version_name = "my version"

        filename = "tiny1.bin"
        FILE_CONTENTS = os.urandom(2 ** 16)
        with open(filename, 'wb') as f:
            f.write(FILE_CONTENTS)

        classifier_name = "tiny2.pth"
        CLASSIFIER_CONTENTS = os.urandom(2 ** 16)
        with open(classifier_name, 'wb') as f:
            f.write(CLASSIFIER_CONTENTS)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--artifact", "model",
             filename],
        )
        assert result.exception
        assert "the key \"model\" is reserved for model" in result.output

        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--artifact", "file",
             filename, "--artifact", "file", filename],
        )
        assert result.exception
        assert "cannot have duplicate artifact keys" in result.output

        runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--artifact", "file",
             filename],
        )
        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--artifact", "file",
             filename],
        )
        assert result.exception
        assert "key \"file\" already exists" in result.output

        os.remove(filename)
        os.remove(classifier_name)

    def test_create_version_wrong_model_name(self, strs):
        version_name = "my version"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', strs[0], version_name],
        )

        assert result.exception
        assert result.output.strip().endswith("not found")

    def test_create_version_from_run(self, experiment_run, model_for_deployment, registered_model):
        np = pytest.importorskip("numpy")
        model_name = registered_model.name
        version_name = "from_run"

        experiment_run.log_model(model_for_deployment['model'], custom_modules=[])
        experiment_run.log_requirements(['scikit-learn'])

        artifact = np.random.random((36, 12))
        experiment_run.log_artifact("some-artifact", artifact)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--from-run", experiment_run.id],
        )
        assert not result.exception

        model_version = registered_model.get_version(name=version_name)
        assert model_version.name in result.output

        env_str = str(model_version.get_environment())
        assert 'scikit-learn' in env_str
        assert 'Python' in env_str

        assert model_for_deployment['model'].get_params() == model_version.get_model().get_params()
        assert (model_version.get_artifact("some-artifact") == artifact).all()

    def test_create_from_run_with_model_artifact_error(self, experiment_run, registered_model):
        model_name = registered_model.name
        version_name = "from_run"
        error_message = "--from_run cannot be provided alongside other options, except for --workspace"

        filename = "tiny1.bin"
        FILE_CONTENTS = os.urandom(2**16)
        with open(filename, 'wb') as f:
            f.write(FILE_CONTENTS)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--artifact", "file",
             filename, "--from-run", experiment_run.id],
        )
        assert result.exception
        assert error_message in result.output

        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--model", filename,
             "--from-run", experiment_run.id],
        )
        assert result.exception
        assert error_message in result.output

        result = runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "-l", "some label",
             "--from-run", experiment_run.id],
        )
        assert result.exception
        assert error_message in result.output

        os.remove(filename)


class TestGet:
    def test_get_model(self, registered_model):
        model_name = registered_model.name

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'get', 'registeredmodel', model_name],
        )

        assert not result.exception
        assert "name: \"{}\"".format(model_name) in result.output

    def test_get_model_output_json(self, registered_model):
        model_name = registered_model.name

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'get', 'registeredmodel', model_name, "--output=json"],
        )

        assert not result.exception
        model_json_str = result.output.strip().splitlines()[-1]
        model_json = json.loads(model_json_str)
        assert model_json['name'] == model_name

    def test_get_model_wrong_name_error(self, strs):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'get', 'registeredmodel', strs[0]],
        )

        assert result.exception
        assert result.output.strip().endswith("not found")

    def test_get_version(self, registered_model):
        model_name = registered_model.name
        version_name = "my-version"
        model_version = registered_model.get_or_create_version(version_name)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'get', 'registeredmodelversion', model_name, version_name],
        )

        assert not result.exception
        assert "version: \"{}\"".format(version_name) in result.output

    def test_get_version_output_json(self, registered_model):
        model_name = registered_model.name
        version_name = "my-version"
        model_version = registered_model.get_or_create_version(version_name)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'get', 'registeredmodelversion', model_name, version_name, "--output=json"],
        )

        assert not result.exception
        version_json_str = result.output.strip().splitlines()[-1]
        version_json = json.loads(version_json_str)
        assert version_json['version'] == version_name

    def test_get_version_wrong_name_error(self, registered_model, strs):
        model_name = registered_model.name

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'get', 'registeredmodelversion', model_name, strs[0]],
        )

        assert result.exception
        print(result.output.strip())
        assert result.output.strip().endswith("not found")


class TestList:
    def test_list_model(self):
        client = Client()
        model1 = client.get_or_create_registered_model()
        label = model1._msg.name + "label1"
        model1.add_label(label)
        model1.add_label("label2")
        model2 = client.get_or_create_registered_model()
        model = client.get_or_create_registered_model()
        model.add_label(label)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'list', 'registeredmodel', '--filter', "labels == \"{}\"".format(label)],
        )

        assert not result.exception
        assert str(model1._msg.name) in result.output
        assert str(model._msg.name) in result.output

        result = runner.invoke(
            cli,
            ['registry', 'list', 'registeredmodel', "--output=json"],
        )

        assert not result.exception
        assert str(model1._msg.name) in result.output
        assert str(model._msg.name) in result.output
        assert str(model2._msg.name) in result.output

class TestUpdate:
    def test_update_version(self, registered_model):
        model_name = registered_model.name
        version_name = "my version"
        registered_model.get_or_create_version(version_name)

        filename = "tiny1.bin"
        FILE_CONTENTS = os.urandom(2**16)
        with open(filename, 'wb') as f:
            f.write(FILE_CONTENTS)

        classifier_name = "tiny2.pth"
        CLASSIFIER_CONTENTS = os.urandom(2**16)
        with open(classifier_name, 'wb') as f:
            f.write(CLASSIFIER_CONTENTS)


        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'update', 'registeredmodelversion', model_name, version_name, '-l', 'label1', '-l', 'label2', "--artifact", "file", filename, "--model", classifier_name],
        )
        os.remove(filename)
        os.remove(classifier_name)
        assert not result.exception

        model_version = registered_model.get_version(name=version_name)
        assert model_version.get_artifact("file").getvalue() == FILE_CONTENTS
        assert model_version.get_labels() == ["label1", "label2"]
        assert model_version.get_model().getvalue() == CLASSIFIER_CONTENTS

    def test_update_version_invalid_key(self, registered_model):
        model_name = registered_model.name
        version_name = "my version"
        registered_model.get_or_create_version(version_name)

        filename = "tiny1.bin"
        FILE_CONTENTS = os.urandom(2**16)
        with open(filename, 'wb') as f:
            f.write(FILE_CONTENTS)

        classifier_name = "tiny2.pth"
        CLASSIFIER_CONTENTS = os.urandom(2**16)
        with open(classifier_name, 'wb') as f:
            f.write(CLASSIFIER_CONTENTS)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ['registry', 'update', 'registeredmodelversion', model_name, version_name, "--artifact", "model", filename],
        )
        assert result.exception
        assert "the key \"model\" is reserved for model" in result.output

        result = runner.invoke(
            cli,
            ['registry', 'update', 'registeredmodelversion', model_name, version_name, "--artifact", "file", filename, "--artifact", "file", filename],
        )
        assert result.exception
        assert "cannot have duplicate artifact keys" in result.output

        runner.invoke(
            cli,
            ['registry', 'update', 'registeredmodelversion', model_name, version_name, "--artifact", "file", filename],
        )
        result = runner.invoke(
            cli,
            ['registry', 'update', 'registeredmodelversion', model_name, version_name, "--artifact", "file", filename],
        )
        assert result.exception
        assert "key \"file\" already exists" in result.output

        os.remove(filename)
        os.remove(classifier_name)

    def test_model_already_logged_error(self, registered_model):
        model_name = registered_model.name
        version_name = "my version"

        classifier_name = "tiny2.pth"
        CLASSIFIER_CONTENTS = os.urandom(2**16)
        with open(classifier_name, 'wb') as f:
            f.write(CLASSIFIER_CONTENTS)

        runner = CliRunner()
        runner.invoke(
            cli,
            ['registry', 'create', 'registeredmodelversion', model_name, version_name, "--model", classifier_name],
        )

        result = runner.invoke(
            cli,
            ['registry', 'update', 'registeredmodelversion', model_name, version_name, "--model", classifier_name],
        )
        assert result.exception
        assert "a model has already been associated with the version" in result.output

        os.remove(classifier_name)

