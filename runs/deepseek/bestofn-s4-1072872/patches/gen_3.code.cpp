Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* field = fields.data();
    Field* const end = field + fields.size();

    while (field != end)
    {
        if (field->GetNum() == fieldNum)
            return field;
        ++field;
    }

    return FIT_NULL;
}
