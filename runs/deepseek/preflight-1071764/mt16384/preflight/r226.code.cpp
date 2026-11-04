void Mesg::AddField(const Field& field)
{
    const FIT_UINT8 fieldNum = field.GetNum();

    for (std::vector<Field>::iterator it = fields.begin(); it != fields.end(); ++it)
    {
        if (it->GetNum() == fieldNum)
            return;
    }

    fields.push_back(field);
}
