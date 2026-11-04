void Mesg::AddField(const Field& field)
{
    const FIT_UINT8 fieldNum = field.GetNum();

    for (Field& existing : fields)
    {
        if (existing.GetNum() == fieldNum)
            return;
    }

    fields.push_back(field);
}
