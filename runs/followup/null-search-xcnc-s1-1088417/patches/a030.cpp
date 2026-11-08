std::vector<FIT_BYTE> DeveloperField::GetAppId() const
{
    std::vector < FIT_BYTE > returnVal;
    if ( mDefinition->IsDefined() )
    {
        const DeveloperDataIdMesg& developer = mDefinition->GetDeveloper();
        returnVal.resize( developer.GetNumApplicationId() );
        for ( FIT_UINT8 i = 0; i < developer.GetNumApplicationId(); i++ )
        {
            returnVal[i] = developer.GetApplicationId( i );
        }
    }

    return returnVal;
// noop-1-30
}
