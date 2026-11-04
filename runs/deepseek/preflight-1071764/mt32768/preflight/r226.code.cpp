void Mesg::AddField(const Field& field)
{
    const FIT_UINT8 num = field.GetNum();
    for (std::vector<Field>::const_iterator it = fields.begin(); it != fields.end(); ++it)
    {
        if (it->GetNum() == num)
            return;
    }
    fields.push_back(field);
}
