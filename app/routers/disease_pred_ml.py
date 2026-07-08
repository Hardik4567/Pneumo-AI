from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

from app.models.user_master import UserMaster
from app.core.dependencies import get_current_user

from app.schemas.user_master import (
    APIResponse,
    DataResponse,
    DataRequest,
    eResultCode
)

from app.schemas.disease_pred_schema import (
    LoadDatasetResponse,
    CleanDatasetResponse,
    PreprocessResponse,
    TrainRequest,
    TrainResponse,
    EvaluationResponse,
    EDAResponse,
    PredictionResponse
)

from app.services.disease_pred_service import (
    load_dataset_service,
    clean_dataset_service,
    preprocess_dataset_service,
    eda_service,
    train_model_service,
    evaluate_model_service,
    predict_service
)

router = APIRouter()

@router.post(
        "/loadDataset",
        response_model=APIResponse[LoadDatasetResponse]
)
async def load_dataset_route(
    # current_user: UserMaster = Depends(get_current_user)
):

    # if not current_user or not current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Unauthorized"
    #     )
    
    result = await load_dataset_service()

    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description="Dataset loaded successfully"
        ),
        data=result
    )

    
@router.post(
        "/cleanDataset",
        response_model=APIResponse[CleanDatasetResponse]
)
async def clean_dataset__route(
    current_user: UserMaster = Depends(get_current_user)
):
    if not current_user or not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    result = await clean_dataset_service()

    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description= "Dataset cleaned successfully "
        ),
        data=result
    )

@router.post(
        "/preprocessDataset",
        response_model=APIResponse[PreprocessResponse]
)
async def preprocess_dataset_route(
    # current_user:UserMaster = Depends(get_current_user)
):
    # if not current_user or not current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Unauthorized"
    #     )
    result = await preprocess_dataset_service()

    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description="Dataset preprocessed successfully"
        ),
        data=result
    )

@router.post(
    "/eda",
    response_model=APIResponse[EDAResponse]
)
async def get_eda_route(
    current_user: UserMaster = Depends(get_current_user)
):

    if not current_user or not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    try:

        data = await eda_service()

        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Dataset statistics retrieved successfully"
            ),
            data=data
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/trainModel",
    response_model=APIResponse[TrainResponse]
)
async def train_model_route(
    request: DataRequest[TrainRequest],
    # current_user: UserMaster = Depends(get_current_user)
):

    # if not current_user or not current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Unauthorized"
    #     )

    try:

        result = await train_model_service(
            request.data
        )

        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Model trained successfully"
            ),
            data=result
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/evaluateModel",
    response_model=APIResponse[EvaluationResponse]
)
async def evaluate_model_route(
    current_user: UserMaster = Depends(get_current_user)
):

    if not current_user or not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    try:

        result = await evaluate_model_service()

        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Model evaluated successfully"
            ),
            data=result
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/predict",
    response_model=APIResponse[PredictionResponse]
)
async def predict_route(
    patient_name: str = Form(...),
    patient_age: int = Form(...),
    patient_gender: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):

    try:

        result = await predict_service(
            file=file,
            db=db,
            patient_name=patient_name,
            patient_age=patient_age,
            patient_gender=patient_gender,
            user_id=current_user.id
        )

        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Prediction completed successfully"
            ),
            data=result
        )

    except Exception as e:


        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )