void Mesg::AddField(const Field& field)
{
    const auto fieldNum = field.GetNum();

    for (auto& existingField : fields)
    {
        if (existingField.GetNum() == fieldNum)
            return;
    }

    fields.push_back(field);
}
