void Mesg::AddDeveloperField(const DeveloperField& field)
{
    const auto definition = field.GetDefinition();

    for (auto& devField : devFields)
    {
        if (devField.GetDefinition() == definition)
        {
            devField = field;
            return;
        }
    }

    devFields.push_back(field);
}
