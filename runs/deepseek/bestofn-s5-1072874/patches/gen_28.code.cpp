void Mesg::AddField(const Field& field)
{
    if (fields.empty())
    {
        fields.reserve(16);
        fields.push_back(field);
        return;
    }

    const FIT_UINT8 fieldNum = field.GetNum();
    for (const Field& existingField : fields)
    {
        if (existingField.GetNum() == fieldNum)
            return;
    }

    fields.push_back(field);
}
