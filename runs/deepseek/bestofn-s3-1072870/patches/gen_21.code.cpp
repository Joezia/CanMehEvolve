void Mesg::AddField(const Field& field)
{
    const int num = field.GetNum();

    for (const Field& existing : fields)
    {
        if (existing.GetNum() == num)
            return;
    }

    fields.push_back(field);
}
