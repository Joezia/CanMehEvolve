Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* field = fields.data();
    Field* const end = field + fields.size();

    for (; field != end; ++field)
    {
        if (field->GetNum() == fieldNum)
            return field;
    }

    return FIT_NULL;
}
